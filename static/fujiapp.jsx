"use strict";
// const React = require('react')
// Import below toolbars from Material UI.
const {
  AppBar,
  Button,
  colors,
  createMuiTheme,
  CssBaseline,
  FormControl,
  Grid,
  Icon,
  Input,
  MuiThemeProvider,
  Paper,
  Typography,
  Toolbar,
  withStyles
} = window["material-ui"];

const theme = createMuiTheme({
  palette: {
    primary: {
      main: "#F5F5F5"
    },
    secondary: {
      main: "#FFCCBC"
    }
  }
});

let socket = io.connect(
  "http://" + document.domain + ":" + location.port + "/chat"
);

// FujiApp root component.
class FujiApp extends React.Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <div style={{ display: "flex" }}>
          <NavBar />
          <main style={{ height: "100vh", overflow: "auto", flexGrow: 1 }}>
            <Feed />
            <MessageArea />
          </main>
        </div>
      </MuiThemeProvider>
    );
  }
}

// Material UI design
const NavBar = () => {
  return (
    <div>
      <AppBar position="absolute">
        <Toolbar>
          <div style={{ flexGrow: 1 }}>
            <Typography variant="title" color="inherit">
              Welcome to Fuji Chat!
            </Typography>
          </div>
          <LogoutButton />
        </Toolbar>
      </AppBar>
    </div>
  );
};

// Creact a logout button.
class LogoutButton extends React.Component {
  handleClick(event) {
    window.location.href = "/logout";
  }

  render() {
    return (
      <div style={{ float: "right" }}>
        <Button
          onClick={this.handleClick}
          variant="contained"
          color="secondary"
        >
          Logout
        </Button>
      </div>
    );
  }
}

// MessageArea component that's a child of FujiApp root component
class MessageArea extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // Current value as placeholder.
      value: ""
    };
    this.handleOnChange = this.handleOnChange.bind(this);
    this.handleOnClick = this.handleOnClick.bind(this);
  }

  // to update this.state.value everytime something is typed before submit.
  handleOnChange(event) {
    this.setState({ value: event.target.value });
  }

  handleOnClick(event) {
    socket.emit("update", { value: this.state.value });
    this.setState({ value: "" });
  }

  // Material UI send button.
  render() {
    return (
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          margin: 20
        }}
      >
        <Paper>
          <div style={{ padding: 10 }}>
            <Grid container spacing={8} alignItems="flex-end">
              <Grid item xs>
                <Input
                  disableUnderline
                  fullWidth
                  placeholder="Messages"
                  value={this.state.value}
                  onChange={this.handleOnChange}
                />
              </Grid>
              <Grid item>
                <Button
                  disabled={this.state.value === ""}
                  onClick={this.handleOnClick}
                  variant="contained"
                  color="secondary"
                >
                  Send
                  <Icon>send</Icon>
                </Button>
              </Grid>
            </Grid>
          </div>
        </Paper>
      </div>
    );
  }
}

// Feed component that's a child of FujiApp root component.
class Feed extends React.Component {
  constructor(props) {
    super(props);
    this.state = { messages: [], language: " " };
    this.scrollToBottom = this.scrollToBottom.bind(this);
  }

  // Show initial log in feedpage history.
  // Fetch default is not work with cookies. To be able to use session
  // add credentials:include.
  // Use componentWillMount to get messages and lanuages before render.
  componentWillMount() {
    socket.on("response", msg_evt => {
      // Use Spread to append msg_evt to the feed area.
      this.setState({ messages: [...this.state.messages, msg_evt] });
    });
    fetch("/messages", { credentials: "include" })
      .then(response => response.json())
      .then(data => this.setState({ messages: data }));
    fetch("/languages", { credentials: "include" })
      .then(response => response.json())
      .then(data =>
        this.setState({ language: data["language"], user: data["user"] })
      );
  }

  scrollToBottom() {
    this.el.scrollIntoView({ block: "end", behavior: "smooth" });
  }

  componentDidUpdate() {
    this.scrollToBottom();
  }

  render() {
    let messages = this.state.messages;
    let userLanguage = this.state.language;
    let user = this.state.user;
    // React for loop.
    let messageList = messages.map(function(message) {
      let translationList = message.translations.map(function(translation) {
        if (
          translation.language === userLanguage &&
          message.text !== translation.text
        ) {
          return <span>{translation.text}</span>;
        }
      });
      if (message.author_id !== user) {
        return (
          <p>
            {message.author}
            <br />
            {message.text}
            <br />
            {translationList}
          </p>
        );
      } else {
        return (
          <p>
            {message.author}
            <br />
            {message.text}
          </p>
        );
      }
    });
    return (
      <Typography>
        <div
          style={{ margin: 10, paddingBottom: 100, marginTop: 75 }}
          ref={el => {
            this.el = el;
          }}
        >
          {messageList}
        </div>
      </Typography>
    );
  }
}

// render start
ReactDOM.render(<FujiApp />, document.getElementById("root"));
// render end
