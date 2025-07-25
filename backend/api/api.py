from db.database import Database
from .settings import Settings
from .mapping import Mapping
from core.parser import Parser
import support.utils as utils
from typing import Literal

class API:
    def __init__(self, *, db: Database):
        self.settings: Settings = Settings(db)
        self.mapping: Mapping = Mapping(db)

    def generate_azure_csv(self, content: str, file_name: str) -> dict[str, str]:
        '''Generates the Azure CSV file for bulk accounts.
        
        Parameters
        ----------
            content: str
                A base64 string representing an Excel file.
            
            file_name: str
                Name of the file given with the content.
        '''
        delimited: list[str] = content.split(',')

        # could add csv support here, for now it will be excel.
        # NOTE: this could be useless because my front end already has this check.
        if('spreadsheet' not in delimited[0].lower()):
            return utils.generate_response(message='Incorrect file entered, got file TYPE_HERE')

        b64_string: str = delimited[-1]

        parser: Parser = Parser(b64_string)
        
        default_headers: dict[str, str] = self.mapping.get_default_data(map_type='headers')
        default_opco: dict[str, str] = self.mapping.get_default_data(map_type='opco')

        validate_dict: dict[str, str] = parser.validate_df(
            default_headers=default_headers, default_opco=default_opco
        )

        if validate_dict.get('status', 'error') == 'error':
            return utils.generate_response(status='error', message=f'Invalid file \
                {file_name} uploaded.')

        names: list[str] = parser.get_names(col_name=default_headers['name'])
        usernames: list[str] = parser.get_usernames(names=names, opco_map=self.mapping.get_table_data('opco'))
        passwords: list[str] = parser.get_passwords()

        utils.generate_csv(names=names, usernames=usernames, passwords=passwords,
            file_path=self.get_output_dir())

        return utils.generate_response(status='success', message=f'Generated CSV file for {file_name}.')
    
    def generate_manual_csv(self, content: list[dict[str, str]]) -> dict[str, str]:
        '''Generates the Azure CSV file for bulk accounts through the manual input.'''
        names: list[str] = []
        usernames: list[str] = []

        seen_names: dict[str, int] = {}

        # contains name, opco, and id. id is not relevant to this however.
        # i could also possibly add in the block sign in values in the content...
        for obj in content:
            # FIXME: let's add a validation here before something breaks.
            name: str = utils.validate_name(obj['name'])
            names.append(name)

            # assume duplicate names are unique, a number is added to distinguish the username.
            if name not in seen_names:
                seen_names[name] = 1
            else:
                seen_names[name] = seen_names.get(name) + 1

                name = name + str(seen_names.get(name))

            opco: str = obj['opco']
            username: str = utils.generate_username(name, func=lambda x: x.replace(' ', '.'), 
                opco=opco, opco_map=self.mapping.get_table_data('opco'))

            usernames.append(username)
        
        passwords: list[str] = [utils.generate_password() for _ in range(len(names))]
        
        utils.generate_csv(
            names=names, usernames=usernames, passwords=passwords, file_path=self.get_output_dir()
        )

        return utils.generate_response(status='success', message='')

    def get_output_dir(self) -> str:
        '''Retrieve the output directory.'''
        key: str = 'output_dir'

        return self.settings.get_setting(key)
    
    def update_output_dir(self) -> dict[str, str]:
        '''Update the output directory.'''
        from tkinter.filedialog import askdirectory

        new_dir: str = askdirectory()
    
        if new_dir == '':
            return
        
        set_sql: str = f'value = "{new_dir}"'
        where: str = f'key = "output_dir"'

        self.settings.update_setting(set_sql=set_sql, where=where)