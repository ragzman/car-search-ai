import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';

import { webSocket } from 'rxjs/webSocket';
import { HttpHeaders } from '@angular/common/http';
import { Observer } from 'rxjs';

// TODO: move this to some model package. 
export interface ChatMessage {
  sender: string;
  message: string;
  type: string;
}


@Component({
  selector: 'ai-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements AfterViewChecked {


  chatHistory: ChatMessage[] = [];
  userInput: string = '';
  loading: boolean = false;

  sendMessage() {
    const socketUrl = 'ws://localhost:8000/aichat'; // Replace with your WebSocket URL

    const headers = new HttpHeaders({
      // Add any necessary headers for authentication or other purposes
    });

    const socket = webSocket({
      url: socketUrl,
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

    const msg = { message: this.userInput, sender: "you", type: "stream" };
    this.chatHistory.push(msg)
    console.log(`Message sent: ${msg}`)

    const observer: Observer<any> = {
      next: (data: any) => {
        // console.log(`Message Received: ${data}`)
        const receivedMsg: ChatMessage = JSON.parse(data) as ChatMessage
        // console.log(`Message Received: ${receivedMsg}`)
        
        // TODO: validate the incoming message. 
        // Handle received data from the backend
        // and update the chat history
        this.chatHistory.push(receivedMsg);
        // this.chatHistory.map(h => {
          // console.log(`Messages in chat history: sender: ${h.sender}, message: ${h.message}, type: ${h.type}.`)})
      },
      error: (error: any) => console.error('WebSocket error:', error),
      complete: () => console.log('WebSocket connection completed.')
    };

    // Subscribe to the socket using the observer
    socket.subscribe(observer);

    // Send the message to the backend
    socket.next(msg);

    // Clear the user input field
    this.userInput = '';
  }


  @ViewChild('scrollableAreaRef', { static: false }) scrollableAreaRef!: ElementRef;

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  scrollToBottom() {
    try {
      this.scrollableAreaRef.nativeElement.scrollTop = this.scrollableAreaRef.nativeElement.scrollHeight;
    } catch (err) { }
  }


}
