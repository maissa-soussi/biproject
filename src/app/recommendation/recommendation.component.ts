import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.css']
})
export class RecommendationComponent implements OnInit {
  public countries: any = []
  public cities: any = []
  user: any
  country: any
  recommandation: any = []
  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.http.get<any>("http://localhost:5000/country")
        .subscribe(
          (result) => {
            this.countries = result;
            console.log(this.countries);           
          },
          (error) => {console.log(error); }
        )
  }

  getCity(country:any): void {
    this.http.get<any>("http://localhost:5000/city/" + country)
        .subscribe(
          (result) => {
            this.cities = result;          
          },
          (error) => {console.log(error); }
        )
  }
  recommendation(): void{
    this.http.post("http://127.0.0.1:5000/recomm",this.user).subscribe(
      (result) => {
        this.recommandation = result;          
      },
      (error) => {console.log(error); }
    );
    
    
  }

  chosenCountry(t:any){
    this.country=t.value;
    
  }

}
