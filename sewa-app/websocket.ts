class WebSocketManager {
    private static instance : WebSocket | null = null;

    private static url: string = 'ws://192.168.0.223/ws/';
    
   
    private constructor (){}

    public static getInstance(): WebSocket {
        if (WebSocketManager.instance === null){
            WebSocketManager.instance = new WebSocket(WebSocketManager.url)
        }
        return WebSocketManager.instance
    }

    public static resetInstance(): void{
        WebSocketManager.instance = null;
    }
    

}
export default WebSocketManager