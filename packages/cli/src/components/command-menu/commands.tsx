import type { Command } from "./types";

export const COMMANDS: Command[] = [
    {
        name:"new",
        description:"Start a new conversation",
        value:"/new",
    },
    {
        name:"agents",
        description:"Switch between agents",
        value:"/agents",
    },
    {
        name:"models",
        description:"Select AI model for generation",
        value:"/models",
    },
    {
        name:"sessions",
        description:"Manage conversation sessions",
        value:"/sessions",
    },
    {
        name:"theme",
        description:"Change the color theme",
        value:"/theme",
    },
    {
        name:"login",
        description:"Log in to your account",
        value:"/login",
    },
    {
        name:"logout",
        description:"Log out of your account",
        value:"/logout",
    },
    {
        name:"upgrade",
        description:"Buy more credits or upgrade your plan",
        value:"/upgrade",
    },
        {
        name:"usage",
        description:"Open billing portal in your browser",
        value:"/usage",
    },
    {
        name:"exit",
        description:"Exit the application",
        value:"/exit",
        action:(ctx)=>{
            ctx.exit();
        },
    },
]