import { Component, inject } from '@angular/core';
import { Breakpoints, BreakpointObserver } from '@angular/cdk/layout';
import { map } from 'rxjs/operators';


@Component({
  selector: 'app-home-dash',
  templateUrl: './home-dash.component.html',
  styleUrls: ['./home-dash.component.css']
})
export class HomeDashComponent {
  private breakpointObserver = inject(BreakpointObserver);

  /** Based on the screen size, switch from standard to one column per row */
  cards = this.breakpointObserver.observe(Breakpoints.Handset).pipe(
    map(({ matches }) => {
      if (matches) {
        return [
          { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 2, url: '/assets/posts/home.md' },
          { title: 'Revolutionize Your Website Experience with AI-Powered Chatbots', cols: 1, rows: 3, url: '/assets/posts/aboutus.md' },
          { title: 'Welcome to Chatables.ai', cols: 1, rows: 3, url: '/assets/posts/whatIsChatables.ai.md' },
          { title: 'Services', cols: 1, rows: 1, url: '/assets/posts/services.md' }
        ];
      }

      return [
        { title: 'Effortless Navigation and Enhanced User Journeys', cols: 2, rows: 2, url: '/assets/posts/home.md' },
        { title: 'Revolutionize Your Website Experience with AI-Powered Chatbots', cols: 1, rows: 3, url: '/assets/posts/aboutus.md' },
        { title: 'Welcome to Chatables.ai', cols: 1, rows: 3, url: '/assets/posts/whatIsChatables.ai.md' },
        { title: 'Services', cols: 1, rows: 1, url: '/assets/posts/services.md' }
      ];
    })
  );
}
