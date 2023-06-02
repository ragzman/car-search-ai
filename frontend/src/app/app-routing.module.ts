import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { PostsComponent } from './home/posts/posts.component';

const routes: Routes = [
  { path: 'chatbot', component: ChatbotComponent },
  { path: 'posts/post/:article', component: PostsComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
