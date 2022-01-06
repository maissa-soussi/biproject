import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.css']
})
export class RecommendationComponent implements OnInit {
  public countries: any = []
  public cities: any = []
  constructor() { }

  ngOnInit(): void {
  }

  recommendation(){
    
    
  }

}
