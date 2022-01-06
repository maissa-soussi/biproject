import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { RecommendationComponent } from './recommendation/recommendation.component';

const routes: Routes = [
  {
    path: "",
    component: DashboardComponent
  },
  {
    path: "Recommendation",
    component: RecommendationComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
