// Once the HTML has loaded, set listeners to all interactive elements
document.addEventListener("DOMContentLoaded", function () {
  // Follow button on profile page
  const followButton = document.querySelector("#user-follow");
  if (followButton) {
    followButton.addEventListener("click", un_follow);
  }

  // Hide all post edit boxes
  const editBoxes = document.getElementsByClassName("post-edit-box");
  for (let i = 0; i < editBoxes.length; i++) {
    editBoxes[i].style.display = "none";
  }

  // Add listener to all post Edit buttons
  const editButtons = document.getElementsByClassName("post-edit-btn");
  for (let i = 0; i < editButtons.length; i++) {
    editButtons[i].addEventListener("click", edit_post);
  }

  // Add listener to all post Like buttons
  const likeButtons = document.getElementsByClassName("like-btn");
  for (let i = 0; i < likeButtons.length; i++) {
    likeButtons[i].addEventListener("click", un_like);
  }
});

//----------------------------------------------------
// Function to extract CSRF token from cookies, as per DJANGO documentation
// https://docs.djangoproject.com/en/3.2/ref/csrf/
//----------------------------------------------------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

//-----------------------------------------------------------------------
// Function to (Un)Follow - triggered when (un)follow button is pressed
// Asynchronously checks if unfollow request was successful
//-----------------------------------------------------------------------
async function un_follow() {
  // Get current follower data from the HTML
  const buttonText = document.querySelector("#user-follow").innerHTML;
  const profile = document.querySelector("#profile-name").innerHTML.slice(1);
  const followerCount = parseInt(
    document.querySelector("#follower-count").innerHTML
  );

  // Prepare PUT request path
  const fetchThis = `profile=${profile}`;

  // Prepare JSON - depending on current Follow button text
  let json = {};
  buttonText === "Unfollow" ? (json.follow = false) : (json.follow = true);
  let data = JSON.stringify(json);
  const csrftoken = getCookie("csrftoken");

  // Send PUT request
  fetch(fetchThis, {
    method: "PUT",
    body: data,
    headers: { "X-CSRFToken": csrftoken },
  }).then((response) => {
    //When response is received
    localStorage.clear();
    if (response.status === 204) {
      // If successful PUT request
      if (buttonText === "Follow") {
        // Switch the values displayed in HTML, don't reload
        document.querySelector("#user-follow").innerHTML = "Unfollow";
        document.querySelector("#follower-count").innerHTML = followerCount + 1;
      } else {
        document.querySelector("#user-follow").innerHTML = "Follow";
        document.querySelector("#follower-count").innerHTML = followerCount - 1;
      }
    }
  });
}

//-----------------------------------------------------------------------
// Function to Edit a post - triggered when Edit button is pressed
// This function does not check if saving the post was successful
//-----------------------------------------------------------------------
function edit_post() {
  // Find which post the function was triggered for
  const id = this.id.slice(10);
  // Get all necessary HTML elements on the post
  const buttonID = `#edit-post-${id}`;
  const textBoxID = `#post-edit-${id}`;
  const messageID = `#post-message-${id}`;
  const buttonText = document.querySelector(buttonID).innerHTML;

  // If Edit button - display textbox to edit the post
  if (buttonText === "Edit Y") {
    document.querySelector(textBoxID).value =
      document.querySelector(messageID).innerHTML;
    document.querySelector(messageID).style.display = "none";
    document.querySelector(textBoxID).style.display = "block";
    document.querySelector(buttonID).innerHTML = "Save";
    // If Save button - display the post text and send PUT request to DB
  } else {
    document.querySelector(messageID).innerHTML =
      document.querySelector(textBoxID).value;
    document.querySelector(messageID).style.display = "block";
    document.querySelector(textBoxID).style.display = "none";
    document.querySelector(buttonID).innerHTML = "Edit Y";

    // Prepare PUT request
    const fetchThis = `edit_post =${id}`;
    const json = {
      message: document.querySelector(textBoxID).value,
      postID: id,
    };
    const csrftoken = getCookie("csrftoken");
    // Send PUT request
    fetch("edit", {
      method: "PUT",
      body: JSON.stringify(json),
      headers: { "X-CSRFToken": csrftoken },
    });
  }
}

//-----------------------------------------------------------------------
// Function to (Un)Like - triggered when (un)like button is pressed
// This function does not check if Liking the post was successful
//-----------------------------------------------------------------------
function un_like() {
  // Find which post the function was triggered for
  const id = this.id.slice(10);
  // Get all necessary HTML elements on the post
  const buttonID = `#post-like-${id}`;
  const button = document.querySelector(buttonID);
  const likers = document.querySelector(`#post-likecount-${id}`).innerHTML;

  // Prepare the PUT message
  const csrftoken = getCookie("csrftoken");
  let json = {};
  json.postID = id;

  // If Like button - Change the HTML elements and send Like = True
  if (button.alt === "LikeButton") {
    button.alt = "UnlikeButton";
    button.src = "https://i.imgur.com/lfLUHWY.png";
    document.querySelector(`#post-likecount-${id}`).innerHTML =
      1 + parseInt(likers);
    json.like = true;
    // If UnLike button - Change the HTML elements and send Like = False
  } else if (button.alt === "UnlikeButton") {
    console.log("Going to Unlike");
    button.alt = "LikeButton";
    button.src = "https://i.imgur.com/sRKJB1k.png";
    document.querySelector(`#post-likecount-${id}`).innerHTML = likers - 1;
    json.like = false;
    // If unexpected value on (Un)Like button - log to debug
  } else {
    console.log("This should not be possible, need to debug");
  }

  // Send PUT request
  fetch("like", {
    method: "PUT",
    body: JSON.stringify(json),
    headers: { "X-CSRFToken": csrftoken },
  });
}
