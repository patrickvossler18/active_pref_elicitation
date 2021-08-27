import React from 'react';
import PairwiseComparison from './PairwiseComparison';
import {
	Col,
	FormGroup,
	Label,
	Row,
    Container
} from 'reactstrap';


class Step extends React.Component{
    constructor(props) {
        super(props)
        this.stepNum = this.props.stepNum; // which step is this
        this.currentStep = this.props.currentStep; // which step is the app currently on?
        this.data = this.props.data;
        this.loading = this.props.loading;
        this.userChoices = this.props.userChoices;
        this.incrementStep = this.props.incrementStep;
    }

    render() { 
        if(this.currentStep !== this.stepNum ){
            // console.log("I am step "+ this.stepNum+ " and I am hidden." + " the current step is " + this.currentStep);
            return null
        }
        return(
            <div className="container">
                <PairwiseComparison
                    // title={this.data['query_title']}
                    title={"TEST"}
                    cardContents={this.data['cardData']}
                    loading={this.loading}
                    userChoices = {this.userChoices}
                    incrementStep={this.incrementStep}
                    // pass userChoices all the way to PairwiseComparisons and from their lift up state by pushing
                    // choices back to userChoices in App's state

                />
            </div>
        );
    }
}

class StepList extends React.Component{
    constructor(props) {
        super(props)
        this.userChoices = this.props.userChoices;
        this.maxSteps = this.props.maxSteps;
        this.choiceData = this.props.choiceData;
        this.currentStep = this.props.currentStep;
        this.loading = this.props.loading;
        this.incrementStep = this.props.incrementStep;
    }



    render() {
        var numSteps = Array(this.maxSteps).fill().map((element,index) => index+1);
        // var contents = numSteps.map((elem) => {

        //     return (
        //         <Step key={elem.toString()} stepNum={elem} currentStep={this.currentStep}
        //          data={this.choiceData[elem]} loading={this.loading} userChoices={this.userChoices}
        //          incrementStep={this.incrementStep}/>
        //     );
        // });
        return(
            <Container>
                {
                    numSteps.map((elem) => {
                            return (
                            <Step key={elem.toString()} stepNum={elem} currentStep={this.currentStep}
                             data={this.choiceData[elem-1]} loading={this.loading} userChoices={this.userChoices}
                             incrementStep={this.incrementStep}/> 
                             );
                    })
                }
            </Container>
        )    
    }
}

export default StepList;