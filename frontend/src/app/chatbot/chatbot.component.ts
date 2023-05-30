import { Component, ElementRef, ViewChild, AfterViewChecked, OnInit, OnDestroy } from '@angular/core';
import { Observer, Subscription } from 'rxjs';
import { ChatService } from './chat.service';


@Component({
    selector: 'ai-chatbot',
    templateUrl: './chatbot.component.html',
    styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements OnInit, AfterViewChecked, OnDestroy {
    chatHistory: ChatMessage[] = [];
    userInput: string = '';
    loading: boolean = false;
    private socketSubscription: Subscription | undefined;
    @ViewChild('scrollableAreaRef', { static: false }) scrollableAreaRef!: ElementRef;


    constructor(private socketioService: ChatService) { }

    ngOnInit() {
        this.socketSubscription = this.socketioService.getMessages().subscribe((receivedMsg: ChatMessage) => {
            if (receivedMsg.type === MessageType.STREAM_MSG) {
                console.log(receivedMsg)
                const lastBotMessageIndex = this.chatHistory.length - 1
                const lastMsg = this.chatHistory[lastBotMessageIndex]
                if (lastMsg.sender == MessageSender.AI) {
                    this.chatHistory[lastBotMessageIndex].message += receivedMsg.message;
                } else {
                    this.chatHistory.push(receivedMsg)
                }
            } else if (receivedMsg.type == MessageType.STREAM_END) {
                this.loading = false
                console.log(receivedMsg) //TODO: remove this and do something else. 
            }
        });
    }

    ngOnDestroy() {
        if (this.socketSubscription) {
            this.socketSubscription.unsubscribe();
        }
    }

    sendMessage() {
        const msg: ChatMessage = {
            message: this.userInput,
            sender: MessageSender.HUMAN,
            type: MessageType.CLIENT_QUESTION
        };
        this.chatHistory.push(msg);
        this.loading = true;

        this.socketioService.sendMessage(this.userInput);

        this.userInput = '';
    }

    ngAfterViewChecked(): void {
        this.scrollToBottom();
    }

    scrollToBottom() {
        try {
            this.scrollableAreaRef.nativeElement.scrollTop = this.scrollableAreaRef.nativeElement.scrollHeight;
        } catch (err) { }
    }
}


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


