import React  from 'react';
import './About.css';
import NavMenu from '../NavMenu'

function About(props) {

    return (
        <React.Fragment>
            <NavMenu />
            <main className='aboutPage'>
                <h3>About</h3>
                <p>This Application is about to visibly explain the predictions of an binary classifier machine learning model. 
                 You have to login via Github and authorize this Application to use your User Information</p>
                <h5>Authors</h5>
                <ul>
                    <li>Konstantin Strassheim</li>
                    <li>Aleksej Strassheim</li>
                </ul>
            </main>
        </React.Fragment>
      );
    }
export default About;