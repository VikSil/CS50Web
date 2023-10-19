// Once the HTML has loaded, set listeners to all interactive elements
document.addEventListener("DOMContentLoaded", function () {
  const followButton = document.querySelector("#user-follow");
  if (followButton) {
    followButton.addEventListener("click", un_follow);
  }

  const editBoxes = document.getElementsByClassName("post-edit-box");
  for (let i = 0; i < editBoxes.length; i++) {
    editBoxes[i].style.display = "none";
  }

  const editButtons = document.getElementsByClassName("post-edit-btn");
  for (let i = 0; i < editButtons.length; i++) {
    editButtons[i].addEventListener("click", edit_post);
  }

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

async function un_follow() {
  //This needs optimisation
  const buttonText = document.querySelector("#user-follow").innerHTML;
  const profile = document.querySelector("#profile-name").innerHTML.slice(1);
  const followerCount = parseInt(
    document.querySelector("#follower-count").innerHTML
  );
  console.log(profile);
  console.log(followerCount);
  const fetchThis = `profile=${profile}`;
  console.log(fetchThis);
  let json = {};

  if (buttonText === "Unfollow") {
    console.log("Going to unfollow");
    json.follow = false;
  } else {
    console.log("Going to follow");
    json.follow = true;
  }

  let data = JSON.stringify(json);
  const csrftoken = getCookie("csrftoken");

  fetch(fetchThis, {
    method: "PUT",
    body: data,
    credentials: "same-origin", //is this even necessary?? test without it
    headers: { "X-CSRFToken": csrftoken },
  }).then((response) => {
    localStorage.clear();
    console.log(response);
    console.log(response.status);
    if (response.status === 204) {
      if (buttonText === "Follow") {
        document.querySelector("#user-follow").innerHTML = "Unfollow";
        document.querySelector("#follower-count").innerHTML = followerCount + 1;
      } else {
        document.querySelector("#user-follow").innerHTML = "Follow";
        document.querySelector("#follower-count").innerHTML = followerCount - 1;
      }
    }
  });
}

function edit_post() {
  const id = this.id.slice(10);
  console.log(id);

  const buttonID = `#edit-post-${id}`;
  const textBoxID = `#post-edit-${id}`;
  const messageID = `#post-message-${id}`;
  const buttonText = document.querySelector(buttonID).innerHTML;

  if (buttonText === "Edit Y") {
    document.querySelector(textBoxID).value =
      document.querySelector(messageID).innerHTML;
    document.querySelector(messageID).style.display = "none";
    document.querySelector(textBoxID).style.display = "block";
    document.querySelector(buttonID).innerHTML = "Save";
  } else {
    document.querySelector(messageID).innerHTML =
      document.querySelector(textBoxID).value;
    document.querySelector(messageID).style.display = "block";
    document.querySelector(textBoxID).style.display = "none";
    document.querySelector(buttonID).innerHTML = "Edit Y";

    const fetchThis = `edit_post =${id}`;
    const json = {
      message: document.querySelector(textBoxID).value,
      postID: id,
    };
    const csrftoken = getCookie("csrftoken");

    fetch("edit", {
      method: "PUT",
      body: JSON.stringify(json),
      headers: { "X-CSRFToken": csrftoken },
    });
  }
}

async function un_like() {
  const id = this.id.slice(10);
  console.log(id);
  const buttonID = `#post-like-${id}`;

  console.log(buttonID);
  const button = document.querySelector(buttonID);
  console.log(button);
  const likers = document.querySelector(`#post-likecount-${id}`).innerHTML;
  console.log(likers);

  let json = {};

  if (button.alt === "LikeButton") {
    console.log("Going to Like");
    button.alt = "UnlikeButton";
    button.src = "https://i.imgur.com/otvk4cY.png";
    document.querySelector(`#post-likecount-${id}`).innerHTML =
      1 + parseInt(likers);
    json.like = true;
    json.postID = id;
  } else if (button.alt === "UnlikeButton") {
    console.log("Going to Unlike");
    button.alt = "LikeButton";
    button.src = "https://i.imgur.com/cU9dp5s.png";
    document.querySelector(`#post-likecount-${id}`).innerHTML = likers - 1;
    json.like = false;
    json.postID = id;
  } else {
    console.log("This should not be possible, need to debug");
  }

  const csrftoken = getCookie("csrftoken");
  fetch("like", {
    method: "PUT",
    body: JSON.stringify(json),
    headers: { "X-CSRFToken": csrftoken },
  });
}

//----------------------------------------------------
// Function to extract CSRF token from cookies, as per DJANGO official docs
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
