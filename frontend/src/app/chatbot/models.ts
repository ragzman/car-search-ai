// TODO: move this to some model package. 
export interface ChatMessage {
    sender: Sender;
    message: string;
    type: MessageType;
}

// Keep in sync with main.py
export enum MessageType {
    STREAM_START,
    STREAM_END,
    STREAM_MSG,
    COMMAND,
    CLIENT_QUESTION,
}

export enum Sender {
    HUMAN,
    AI,
}