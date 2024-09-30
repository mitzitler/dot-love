import { useState, useEffect } from "react";
import { GenericHeader } from "./GenericHeader";
import '../App.css';

export function GenericBody({body}) {
    return (
        <div class="generic-body">
            {body}
            <ul>i am information</ul>
            <ul>more information</ul>
        </div>
    )
}