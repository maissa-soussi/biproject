import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  destinationVar=false
  airlineVar=false
  public destinations: any = {}
  public airlines: any = {}
  constructor(private router: Router) { }

  ngOnInit(): void {
  }

  destination(){
    this.destinationVar=true
    this.airlineVar=false
  }

  airline(){
    this.airlineVar=true
    this.destinationVar=false
  }

  recommendation(){
    this.router.navigate(['/Recommendation'])
  }

}
