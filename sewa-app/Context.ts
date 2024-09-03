import { createContext } from 'react';
type ContextProps = {
    message: string 
    startTime?: string
}
const ActionContext = createContext<ContextProps>({'message' : 'nothing'});
export default ActionContext;