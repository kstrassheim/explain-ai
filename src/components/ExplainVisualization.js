import React  from 'react';
import { Bar } from 'react-chartjs-2';

function ExplainVisualization(props) {

    const posLabels = props.explainResult ? Object.keys(props.explainResult).filter(k=>props.explainResult[k]>=0.0) : [];
    const negLabels = props.explainResult ? Object.keys(props.explainResult).filter(k=>props.explainResult[k]<0.0) : [];

    const data = props.explainResult ?  {
            labels: props.explainResult ? Object.keys(props.explainResult) : [],
            datasets:[
                {
                    label:'Positive',
                    data: props.explainResult ? Object.keys(props.explainResult).map(k=>posLabels.filter(o=>o===k).length > 0 ? props.explainResult[k] : 0.0) : [],
                    backgroundColor: 'rgba(255,0,0,0.2)',
                    borderColor: 'rgba(255,0,0,1)',
                    borderWidth: 1,
                    hoverBackgroundColor: 'rgba(255,0,0,0,0.4)',
                    hoverBorderColor: 'rgba(255,0,0,0,1)'
                },
                {
                    label:'Negative',
                    data: props.explainResult ? Object.keys(props.explainResult).map(k=>negLabels.filter(o=>o===k).length > 0 ? props.explainResult[k] : 0.0) : [],
                    backgroundColor: 'rgba(0,0,255,0.2)',
                    borderColor: 'rgba(0,0,255,1)',
                    borderWidth: 1,
                    hoverBackgroundColor: 'rgba(0,0,255,0.4)',
                    hoverBorderColor: 'rgba(0,0,255,1)'
                }
            ]
        } : {};
    return (
        <React.Fragment>
            <section className='explainVisualization'>
                { props.explainResult ? 
                    <Bar data={data} options={{indexAxis:'y'}} />
                    :  <React.Fragment /> 
                }
            </section>
        </React.Fragment>
      );
    }
export default ExplainVisualization;