import { Injectable } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { HttpHeaders } from '@angular/common/http';
import { Observer } from 'rxjs';
import { ChatMessage, MessageSender, MessageType } from './chatbot.component';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private socketUrl = 'ws://localhost:8000/aichat'; // Replace with your WebSocket URL
  private socket: WebSocketSubject<any>;

  constructor() {
    this.socket = this.initializeSocket();
  }

  private initializeSocket() {
    const headers = new HttpHeaders({
      // Add any necessary headers for authentication or other purposes
    });

    const socket = webSocket({
      url: this.socketUrl,
      deserializer: (data: MessageEvent) => JSON.parse(data.data),
      openObserver: {
        next: () => console.log('WebSocket connection established.'),
        error: (error: any) => console.error('WebSocket connection error:', error)
      },
      closeObserver: {
        next: () => console.log('WebSocket connection closed.'),
        error: (error: any) => console.error('WebSocket connection error:', error)
      }
    });
    return socket
  }

  public sendMessage(message: string) {
    const msg: ChatMessage = {
      message: message,
      sender: MessageSender.HUMAN,
      type: MessageType.CLIENT_QUESTION
    };
    console.log(`senidng msg: ${msg.message}, ${msg.type}`)
    this.socket.next(JSON.stringify(msg));
  }

  public subscribe(observer: Observer<any>) {
    this.socket.subscribe(observer);
  }
}
