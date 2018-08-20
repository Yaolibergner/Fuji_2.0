"use strict";

let socket = io.connect(
  "http://" + document.domain + ":" + location.port + "/chat"
);

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
  }
}

// A welcome title.
class Welcome extends React.Component {
  render() {
    return <h3 className="Wecome-title">Welcome to Fuji.</h3>;
  }
}

// MessageArea component that's a child of FujiApp root component
class MessageArea extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // Current value as placeholder.
      value: "Type your message."
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    socket.emit("update", { value: this.state.value });
    event.preventDefault();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <textarea value={this.state.value} onChange={this.handleChange} />
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

// Feed component that's a child of FujiApp root component.
class Feed extends React.Component {
  constructor(props) {
    super(props);
    this.state = { messages: [], language: " " };
    socket.on(
      "response",
      function(msg_evt) {
        // User Spread to append msg_evt to the feed area.
        this.setState({ messages: [...this.state.messages, msg_evt] });
      }.bind(this)
    );
  }

  // Show initial log in feedpage history.
  // Fetch default is not work with cookies. To be able to use session
  // add credentials:include.
  componentWillMount() {
    fetch("/messages", { credentials: "include" })
      .then(response => response.json())
      .then(data => this.setState({ messages: data }));
    fetch("/languages", {credentials: "include"})
      .then(response => response.json())
      .then(data => this.setState({language: data["language"]}))
  }


  render() {
    let messages = this.state.messages;
    let userLanguage = this.state.language;
    // React for loop.
    let messageList = messages.map(function(message) {
      let translationList = message.translations.map(function(translation) {
        if (translation.language === userLanguage) {
        return <span>{translation.text}</span>};
      });
      return (
        <p>
          {message.author}
          <br />
          {message.text}
          <br />
          {translationList}
        </p>
      );
      // here is where I need to figure out clients language.
      // filter out translation by user language.
    });
    console.log(messageList);
    return <div className="messages">{messageList}</div>;
  }
}

// render start
ReactDOM.render(<FujiApp />, document.getElementById("root"));
// render end
