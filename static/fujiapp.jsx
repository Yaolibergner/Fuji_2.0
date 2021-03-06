"use strict";
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
      main: "#2196f3"
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
            {/*    <Typing />*/}
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
            <Typography variant="title" color="grey">
              Bergner's family room!
            </Typography>
          </div>
          <AddNewMember />
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
        <Button id="logout" onClick={this.handleClick} variant="contained">
          Logout
        </Button>
      </div>
    );
  }
}

// Create a add a new member button.
class AddNewMember extends React.Component {
  handleClick(event) {
    window.location.href = "/addmember";
  }

  render() {
    return (
      <div style={{ float: "right", marginRight: "15px" }}>
        <Button
          id="addmember"
          onClick={this.handleClick}
          variant="contained"
          color="secondary"
        >
          Add New Member
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
      value: "",
      // Current typing user.
      user: ""
    };
    this.handleOnChange = this.handleOnChange.bind(this);
    this.handleOnClick = this.handleOnClick.bind(this);
  }

  // to get current user, and then emit to the server to show who is typing.
  componentWillMount() {
    fetch("/languages", { credentials: "include" })
      .then(response => response.json())
      .then(data => this.setState({ user: data["user"] }));
  }

  // to update this.state.value everytime something is typed before submit.
  handleOnChange(event) {
    this.setState({ value: event.target.value });
    // // to send server that client is typing.
    socket.emit("typing", { value: this.state.user });
  }

  // update textarea state, empty textarea once message is sent.
  handleOnClick(event) {
    socket.emit("update", { value: this.state.value });
    this.setState({ value: "" });
  }

  // Allowing enter key to send message.
  enterPressed(event) {
    if (event.key == "Enter") {
      socket.emit("update", { value: this.state.value });
      this.setState({ value: "" });
    }
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
                  id="textarea"
                  disableUnderline
                  fullWidth
                  placeholder="Say something..."
                  value={this.state.value}
                  onChange={this.handleOnChange}
                  onKeyPress={this.enterPressed.bind(this)}
                />
              </Grid>
              <Grid item>
                <Button
                  id="sendbutton"
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
    this.state = { messages: [], language: " ", typing_user: "" };
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
      // Clear out is typing after user sent message.
      if (msg_evt["author_id"] === this.state.typing_user) {
        this.setState({ typing_user: "" });
      }
    });
    fetch("/messages", { credentials: "include" })
      .then(response => response.json())
      .then(data => this.setState({ messages: data }));
    fetch("/languages", { credentials: "include" })
      .then(response => response.json())
      .then(data =>
        this.setState({ language: data["language"], user: data["user"] })
      );

    // setTimeout for istyping to update when user stop typing.
    let timeout;
    socket.on("status", user_evt => {
      let user = this.state.user;
      // Use Spread to append msg_evt to the feed area.
      if (user_evt["value"] !== user) {
        this.setState({ typing_user: user_evt["value"] });
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.setState({ typing_user: "" });
        }, 5000);
      }
    });
  }

  scrollToBottom() {
    this.el.scrollIntoView({ block: "end", behavior: "smooth" });
  }

  // Scrolltobottom when message sent.
  componentDidUpdate() {
    this.scrollToBottom();
  }

  render() {
    let messages = this.state.messages;
    let userLanguage = this.state.language;
    let user = this.state.user;
    let typing_user = this.state.typing_user;
    // React for loop.
    let messageList = messages.map(function(message) {
      let translationList = message.translations.map(function(
        translation,
        index
      ) {
        if (translation.language === userLanguage) {
          return (
            <span key={`translationText${index}`}>{translation.text}</span>
          );
        }
      });
      if (message.author_id !== user) {
        return (
          <div
            style={{
              display: "flex",
              marginTop: "8px",
              marginBottom: "8px",
              flexDirection: "column",
              alignSelf: "flex-start"
            }}
          >
            <Typography>{message.author}</Typography>
            <div
              style={{
                display: "flex",
                justifyContent: "flex-start",
                alignItems: "flex-start"
              }}
            >
              <img
                src={"/uploads/" + message.author_id + ".jpg"}
                style={{
                  marginRight: "8px",
                  width: 40,
                  height: 40,
                  borderRadius: "50%"
                }}
              />

              <div class="hover">
                <div class="hover__no-hover">
                  <Typography
                    style={{
                      backgroundColor: "#ededed",
                      padding: "8px",
                      borderRadius: "1.2em"
                    }}
                  >
                    {translationList}
                  </Typography>
                </div>
                <div class="hover__hover">
                  <Typography
                    style={{
                      backgroundColor: "#ededed",
                      padding: "8px",
                      borderRadius: "1.2em"
                    }}
                  >
                    {message.text}
                  </Typography>
                </div>
              </div>
            </div>
          </div>
        );
      } else {
        return (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              marginTop: "8px",
              marginBottom: "8px",
              alignSelf: "flex-end"
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "flex-start"
              }}
            >
              <Typography
                style={{
                  backgroundColor: "#2196f3",
                  color: "white",
                  padding: "8px",
                  borderRadius: "1.2em"
                }}
              >
                {message.text}
              </Typography>
              <img
                src={"/uploads/" + message.author_id + ".jpg"}
                style={{
                  marginLeft: "8px",
                  width: 40,
                  height: 40,
                  borderRadius: "50%"
                }}
              />
            </div>
          </div>
        );
      }
    });
    let isTyping = "";
    if (typing_user !== "") {
      isTyping = (
        <div>
          <img
            src={"/uploads/" + typing_user + ".jpg"}
            style={{ weight: 20, height: 20, borderRadius: "50%" }}
          />{" "}
          is typing...
        </div>
      );
    }
    return (
      <div
        class="texttesting"
        style={{
          display: "flex",
          flexDirection: "column",
          margin: 10,
          paddingBottom: 100,
          marginTop: 75
        }}
        ref={el => {
          this.el = el;
        }}
      >
        {messageList}
        <Typography>
          <span> {isTyping} </span>
        </Typography>
      </div>
    );
  }
}

// render start
ReactDOM.render(<FujiApp />, document.getElementById("root"));
// render end
