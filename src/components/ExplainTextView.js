import React, { useEffect }  from 'react';
import {Container} from 'react-bootstrap';
import './ExplainList.css';


const explainMappings = {
    'LIME':ExplainTextViewLIME,
    'IterativeLIME':ExplainTextViewLIME,
    'Anchor':ExplainTextViewAnchor,
    'MultiStepLIME':ExplainTextViewMultiStepLIME
}

function ExplainTextViewLIME(props){
    const text = props.result.explainer_result_string_mapped.strings
    const values = props.result.explainer_result_string_mapped.values
    const valuesSum = props.result.explainer_result.reduce((partial_sum, a) => partial_sum + a[1], 0)

    const valuesScaled = values.map((v,i) => v/valuesSum)

    return(
        <React.Fragment>
            {
                text && text.length > 0 ?
                <Container>
                    {text.map((v, index) => <span key={index} style={ values[index] >= 0?
                        {background:`rgba(245, 80,65, ${Math.abs(valuesScaled[index])})`}:
                        {background:`rgba(90, 66,245, ${Math.abs(valuesScaled[index])})`}
                        }>
                            {v}
                            </span>)}
                </Container>
                :
                ''
            }
        </React.Fragment>
    )
}

function ExplainTextViewAnchor(props){
    return(
        <React.Fragment>
            
        </React.Fragment>
    )
}
function ExplainTextViewMultiStepLIME(props){
    // const [mode, setMode] = useState(0)
    if(!props.result.explainer_result_string_mapped || !props.result.explainer_result_string_mapped.strings|| !props.result.explainer_result_string_mapped.strings[0]){
        return props.text;
    }
    
    const text = props.result.explainer_result_string_mapped.strings[props.explain_level]
    const values = props.result.explainer_result_string_mapped.values[props.explain_level]
    const valuesSum = props.result.explainer_result[props.explain_level].reduce((partial_sum, a) => partial_sum + a[1], 0)

    const valuesScaled = values.map((v,i) => v/valuesSum)

    return(
        <React.Fragment>
            {
                text && text.length > 0 ?
                <Container>
                    {text.map((v, index) => <span key={index} style={ values[index] >= 0?
                        {background:`rgba(245, 80,65, ${Math.abs(valuesScaled[index])})`}:
                        {background:`rgba(90, 66,245, ${Math.abs(valuesScaled[index])})`}
                        }>
                            {v}
                            </span>)}
                    
                </Container>
                :
                ''
            }
        </React.Fragment>
    )
}

function ExplainTextView(props) {
    useEffect(() => { 
        if (!props.result || props.result.length < 1) { return; }
      },[props.text, props.result, props.explain_level])
    if (!props || !props.result){
        return props.text
    }



    if(props.result.name && props.result.name in explainMappings){
        return explainMappings[props.result.name](props)
    }
    return (
        <React.Fragment>
            {props.result.name ? props.result.name : 'Undefined'} not implemented.
        </React.Fragment>
 );
}

export default ExplainTextView;