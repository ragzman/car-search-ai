import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { MessageSender, MessageType, ChatMessage } from './chatbot.component';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private socket: Socket;

  constructor() {
    // socket.io is mounted on /sock on the server.
    this.socket = io('/', { path: "/sock/socket.io", });
    this.initSocketListeners();
  }

  private initSocketListeners() {
    this.socket.on('connect', () => {
      //TODO remove
      console.log('Socket.IO connection established.');
    });

    this.socket.on('disconnect', () => {
      //TODO Remove log.
      console.log('Socket.IO connection closed.');
    });
  }

  public sendMessage(message: string) {
    const msg: ChatMessage = {
      message: message,
      sender: MessageSender.HUMAN,
      type: MessageType.CLIENT_QUESTION
    };
    // console.log(`Sending message: ${msg.message}`)
    // console.log(`IsActive ${this.socket.active}: , IsConnected: ${this.socket.connected}, ${this.socket}`)
    this.socket.emit('chat', msg);
  }

  public getMessages(): Observable<ChatMessage> {
    return new Observable<ChatMessage>((observer) => {
      //TODO: we shouldn't have to parse again here. see why we can't directly make data as ChatMessage type.
      this.socket.on('chat', (data) => {
        const cm: ChatMessage = JSON.parse(data)
        observer.next(cm);
      });

      return () => {
        this.socket.off('chat');
      };
    });
  }
}
