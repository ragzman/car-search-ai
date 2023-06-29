import { Component, ElementRef, ViewChild, AfterViewChecked, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { ChatService } from './chatbot.service';
import { EventService } from '../bot-event.service';
import { Directive, OnChanges, Input } from '@angular/core';

@Directive({
    selector: '[scrollToBottom]'
})
export class ScrollToBottomDirective implements OnChanges {
    @Input()
    trigger!: number;

    constructor(private el: ElementRef) { }

    ngOnChanges() {
        this.el.nativeElement.scrollTop = this.el.nativeElement.scrollHeight;
        console.log(this.el.nativeElement.scrollTop)
    }
}

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


    constructor(private chatService: ChatService, private eventService: EventService) { }

    ngOnInit() {
        this.socketSubscription = this.chatService.getMessages().subscribe((receivedMsg: ChatMessage) => {
            // console.log(`Message Received in component.ts: ${receivedMsg}`)
            // console.log(`receviedMsg.type: ${receivedMsg.type}`)
            if (receivedMsg.type === MessageType.STREAM_MSG) {
                const lastBotMessageIndex = this.chatHistory.length - 1
                const lastMsg = this.chatHistory[lastBotMessageIndex]
                if (lastMsg.sender == MessageSender.AI) {
                    this.chatHistory[lastBotMessageIndex].message += receivedMsg.message;
                } else {
                    this.chatHistory.push(receivedMsg)
                }
            } else if (receivedMsg.type == MessageType.STREAM_END) {
                this.loading = false
                //TODO: do something else too? 
            }
            else if (receivedMsg.type == MessageType.COMMAND) {
                //TODO: change format of this command message. 
                // console.log(`emiting event: ${receivedMsg}`)
                this.eventService.emitEvent(receivedMsg.message)
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

        this.chatService.sendMessage(this.userInput);

        this.userInput = '';
    }

    ngAfterViewChecked(): void {
        // this.scrollToBottom();
    }

    // scrollToBottom() {
    //     try {
    //         this.scrollableAreaRef.nativeElement.scrollTop = this.scrollableAreaRef.nativeElement.scrollHeight;
    //     } catch (err) { }
    // }
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


