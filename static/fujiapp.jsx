"use strict";

// Does this usually go globally?
let socket = io.connect('http://' + 'localhost:5000' + '/chat');

// FujiApp root component.
class FujiApp extends React.Component {
  render() {
    return (
      <div className="feedpage">
              <Welcome />
              <Feed />
              <MessageArea />
      </div>
    );
  };
}

// A welcome title.
class Welcome extends React.Component {
  render() {
    return (
      <h3 className="Wecome-title">Welcome to Fuji.</h3>
      );
 };
}

// MessageArea component that's a child of FujiApp root component 
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

// Feed component that's a child of FujiApp root component.
class Feed extends React.Component {
  constructor(props) {
    super(props);
    // this.state need to retrieve message with AJAX call???
    this.state = { messages: [] };
    socket.on('response', function(msg_evt) {
      const message = {text: msg_evt['value'], 
                       translation: msg_evt['translation']}
      this.setState({messages: [...this.state.messages, message]});
    }.bind(this));
  }

  render() {
    let messages = this.state.messages;
    // React for loop.
    let messageList = messages.map(function(message){
      return <p>{message.text}<br></br>{message.translation}</p>;
    })
    return (
      <div className="messages">
        {messageList}
      </div>
    );
  };
}

// render start 
ReactDOM.render(
  <FujiApp />,
  document.getElementById('root')
);
// render end 