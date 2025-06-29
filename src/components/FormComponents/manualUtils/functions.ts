import { Dispatch, useEffect } from "react";
import { ManualData } from "./types";
import { formInputs } from "./vars";

export async function addEntry(
    divRef: React.RefObject<HTMLDivElement|null>,
    setData: Dispatch<React.SetStateAction<ManualData[]>>): Promise<void>{
    if(!divRef.current) return;

    const children: HTMLCollection = divRef.current!.children;
    const objTemp: ManualData = {};

    const objProps: Array<string> = ['name', 'opco'];

    // put this in your notes buddy
    for(let i = 0; i < children.length; i++){
        const input = children[i];
        if(input instanceof HTMLInputElement){
            // FIXME: add an alert for empty name inputs
            if(input.value.trim() == '' && input.id.includes('name')){
                return;
            }

            if(formInputs[i].name == input.id){
                objTemp[objProps[i]] = input.value;
                
                // resets the value if successful
                input.value = '';
            }
        }
    }

    setData(prev => [...prev, objTemp]);
}