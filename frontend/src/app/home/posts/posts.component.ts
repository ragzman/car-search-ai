import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { EventService } from 'src/app/bot-event.service';

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.css']
})
export class PostsComponent implements OnInit {

  post!: string; // add this
  href!: string; // add this

  constructor(private route: ActivatedRoute, private eventService: EventService) { } // Modify this, to add the ActivatedRoute

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      let articleName = params.get('article');
      const path = `./assets/posts/${articleName}.md`;
      this.post = path;
    });

    this.eventService.event$.subscribe((articleName: string) => {
      console.log(`command received: ${articleName}`)
      const path = `./assets/posts/${articleName}.md`;
      this.post = path;
    });
  }

}