"use strict";

// Does this go globally?
let socket = io.connect('http://' + 'localhost:5000' + '/test');

 // MessageArea component that's a child of Fujiapp root component 
class MessageArea extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // Current value as placeholder. 
      value: 'Type your message.'
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    // Need to update here to not replace everything, but append new message.
    socket.emit('update', {value: this.state.value})
    event.preventDefault();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <textarea value={this.state.value}
        onChange={this.handleChange} />
        <input type="submit" value="Submit" />
        </form>
      );
  };
}


 // render start 
ReactDOM.render(
  <MessageArea />,
  document.getElementById('root')
);
 // render end 