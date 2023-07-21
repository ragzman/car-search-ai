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
    }
}

@Component({
    selector: 'ai-chatbot',
    templateUrl: './chatbot.component.html',
    styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements OnInit, AfterViewChecked, OnDestroy {
    chatHistory: ChatMessage[] = [];
    quickActions: string[] = [];
    maxSizeQuickActions: number = 5;
    userInput: string = '';
    loading: boolean = false;
    maxChatHistoryHeight: string;
    private socketSubscription: Subscription | undefined;
    @ViewChild('scrollableAreaRef', { static: false }) scrollableAreaRef!: ElementRef;


    constructor(private chatService: ChatService, private eventService: EventService) {
        // Calculate the dynamic max-height value here based on your requirements
        // For example, you can set it to a percentage of the viewport height
        const percentageOfViewportHeight = 60; // Adjust this value as needed
        const viewportHeight = window.innerHeight;
        this.maxChatHistoryHeight = `${(percentageOfViewportHeight / 100) * viewportHeight}px`;
    }

    ngOnInit() {
        // default chatbot welcome message
        this.chatHistory.push({ message: "Hi, I am Chatables.ai. How can I help you today?", sender: MessageSender.AI, type: MessageType.STREAM_END });
        // this.quickActions.push("Welcome Bubble")
        this.updateQuickActions("Welcome Bubble!")
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
            else if (receivedMsg.type == MessageType.QUICK_ACTION) {
                this.updateQuickActions(receivedMsg.message)
            }
        });
    }

    updateQuickActions(message: string) {
        if (!this.quickActions.includes(message)) {
            this.quickActions.unshift(message);
        }

        if (this.quickActions.length > this.maxSizeQuickActions) {
            // Remove elements from the back of the array
            this.quickActions.splice(this.maxSizeQuickActions);
        }
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

    // For Quick Actions Bubbles
    quickAction(action: string) {
        this.userInput = action;
        this.sendMessage();
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
    QUICK_ACTION = "QUICK_ACTION",
}

export enum MessageSender {
    HUMAN = 'HUMAN',
    AI = 'AI',
}
