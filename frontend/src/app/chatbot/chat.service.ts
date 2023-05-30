import { Injectable } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { HttpHeaders } from '@angular/common/http';
import { Observable, Observer, Subscription } from 'rxjs';
import { MessageSender, MessageType, ChatMessage } from './chatbot.component';
import { io, Socket } from 'socket.io-client';


// @Injectable({
//   providedIn: 'root'
// })
// export class ChatService {

//   private socketUrl = 'ws://localhost:8000/aichat'; // Replace with your WebSocket URL
//   private socket: WebSocketSubject<any>;

//   constructor() {
//     this.socket = this.initializeSocket();
//   }

//   private initializeSocket() {
//     const headers = new HttpHeaders({
//       // Add any necessary headers for authentication or other purposes
//     });

//     const socket = webSocket({
//       url: this.socketUrl,
//       deserializer: (data: MessageEvent) => JSON.parse(data.data),
//       openObserver: {
//         next: () => console.log('WebSocket connection established.'),
//         error: (error: any) => console.error('WebSocket connection error:', error)
//       },
//       closeObserver: {
//         next: () => console.log('WebSocket connection closed.'),
//         error: (error: any) => console.error('WebSocket connection error:', error)
//       }
//     });
//     return socket
//   }

//   public sendMessage(message: string) {
//     const msg: ChatMessage = {
//       message: message,
//       sender: MessageSender.HUMAN,
//       type: MessageType.CLIENT_QUESTION
//     };
//     console.log(`sending msg: ${msg.message}, ${msg.type}`)
//     this.socket.next(JSON.stringify(msg));
//   }

//   public subscribe(observer: Observer<any>): Subscription {
//     return this.socket.subscribe(observer);
//   }
// }

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private socket: Socket;

  constructor() {
    this.socket = io('http://localhost:8000/aichat'); // Replace with your Socket.IO server URL
    this.initSocketListeners();
  }

  private initSocketListeners() {
    this.socket.on('connect', () => {
      console.log('Socket.IO connection established.');
    });

    this.socket.on('disconnect', () => {
      console.log('Socket.IO connection closed.');
    });
  }

  public sendMessage(message: string) {
    const msg: ChatMessage = {
      message: message,
      sender: MessageSender.HUMAN,
      type: MessageType.CLIENT_QUESTION
    };
    this.socket.emit('message', msg);
  }

  public getMessages(): Observable<ChatMessage> {
    return new Observable<ChatMessage>((observer) => {
      this.socket.on('message', (data: ChatMessage) => {
        observer.next(data);
      });

      return () => {
        this.socket.off('message');
      };
    });
  }
}
