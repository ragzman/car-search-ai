import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';

import { webSocket } from 'rxjs/webSocket';
import { HttpHeaders } from '@angular/common/http';
import { Observer } from 'rxjs';

import {ChatService} from './chat.service'


export interface ChatMessage {
  sender: MessageSender;
  message: string;
  type: MessageType;
}

// Keep in sync with main.py
export enum MessageType {
  STREAM_START = "STREAM_START",
  STREAM_END = "STREAM_END",
  STREAM_MSG = "STREAM_MSG",
  COMMAND = "COMMAND",
  CLIENT_QUESTION = "CLIENT_QUESTION",
}

export enum MessageSender {
  HUMAN = 'HUMAN',
  AI = 'AI',
}

@Component({
  selector: 'ai-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})

export class ChatbotComponent implements AfterViewChecked {
  chatHistory: ChatMessage[] = [];
  userInput: string = '';
  loading: boolean = false;  //TODO: start using this to disable the send button.

  constructor(private chatService: ChatService) { }

  sendMessage() {
    const msg: ChatMessage = {
      message: this.userInput,
      sender: MessageSender.HUMAN,
      type: MessageType.CLIENT_QUESTION
    };
    this.chatHistory.push(msg);
    // console.log(`Message sent: ${msg}`)

    const observer: Observer<any> = {
      next: (data: any) => {
        // console.log(`Message Received: ${data}`)
        const receivedMsg: ChatMessage = JSON.parse(data) as ChatMessage
        // console.log(`Message Received: ${receivedMsg}`)

        if (receivedMsg.type === MessageType.STREAM_MSG) {
          const lastBotMessageIndex = this.chatHistory.length - 1
          const lastMsg = this.chatHistory[lastBotMessageIndex]
          if (lastMsg.sender == MessageSender.AI) {
            this.chatHistory[lastBotMessageIndex].message += receivedMsg.message;
          } else {
            this.chatHistory.push(receivedMsg)

          }
        } else {
          console.log(receivedMsg) //TODO: remove this and do something else. 
        }
        // this.chatHistory.map(h => {
        // console.log(`Messages in chat history: sender: ${h.sender}, message: ${h.message}, type: ${h.type}.`)})
      },
      error: (error: any) => console.error('WebSocket error:', error),
      complete: () => console.log('WebSocket connection completed.')
    };

    // Subscribe to the socket using the observer
    this.chatService.subscribe(observer)

    // Send the message to the backend
    this.chatService.sendMessage(msg.message)

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
