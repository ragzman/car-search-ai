import { Component, inject } from '@angular/core';
import { Breakpoints, BreakpointObserver } from '@angular/cdk/layout';
import { map } from 'rxjs/operators';
// import { EventService } from '../bot-event.service';

@Component({
  selector: 'app-home-dash',
  templateUrl: './home-dash.component.html',
  styleUrls: ['./home-dash.component.css']
})
export class HomeDashComponent {
  private breakpointObserver = inject(BreakpointObserver);


  // constructor(private eventService: EventService) { }

  // ngOnInit() {
  //   this.eventService.event$.subscribe(eventMsg => {
  //     console.log('Received event: ', eventMsg);
  //     // Handle the event here.
  //     this.handleEvent(eventMsg);
  //   });
  // }

  // handleEvent(eventMsg: string) {
  //   // Do something with eventMsg
  //   console.log(`Handling event: ${eventMsg}`);
  //   this.cards = this.breakpointObserver.observe(Breakpoints.Handset).pipe(
  //     map(({ matches }) => {
  //       if (matches) {
  //         return [
  //           { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 2, url: '/assets/posts/home.md' },
  //         ];
  //       }

  //       return [
  //         { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 2, url: '/assets/posts/home.md' },
  //       ];
  //     })
  //   );
  // }

  /** Based on the screen size, switch from standard to one column per row */
  cards = this.breakpointObserver.observe(Breakpoints.Handset).pipe(
    map(({ matches }) => {
      if (matches) {
        return [
          { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 1, url: '/assets/posts/home.md' },
          { title: 'Revolutionize Your Website Experience with AI-Powered Chatbots', cols: 2, rows: 1, url: '/assets/posts/aboutus.md' },
          { title: 'Welcome to Chatables.ai', cols: 2, rows: 1, url: '/assets/posts/whatIsChatables.ai.md' },
          { title: 'Services', cols: 2, rows: 1, url: '/assets/posts/services.md' }
        ];
      }

      return [
        { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 1, url: '/assets/posts/home.md' },
        { title: 'Revolutionize Your Website Experience with AI-Powered Chatbots', cols: 2, rows: 1, url: '/assets/posts/aboutus.md' },
        { title: 'Welcome to Chatables.ai', cols: 2, rows: 1, url: '/assets/posts/whatIsChatables.ai.md' },
        { title: 'Services', cols: 2, rows: 1, url: '/assets/posts/services.md' }
      ];
    })
  );
}
