import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  destinationVar=false
  airlineVar=false
  public destinations: any 
  public airlines: any 
  constructor(private router: Router, private http: HttpClient) { }

  ngOnInit(): void {
    this.http.get<any>("http://localhost:5000/destination")
        .subscribe(
          (result) => {
            this.destinations = result;
            console.log(this.destinations);           
          },
          (error) => {console.log(error); }
        );
    
    this.http.get<any>("http://localhost:5000/airline")
        .subscribe(
          (result) => {
            this.airlines = result;
            console.log(this.airlines);           
          },
          (error) => {console.log(error); }
        );
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
