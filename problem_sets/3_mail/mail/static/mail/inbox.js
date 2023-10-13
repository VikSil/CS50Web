// Once the HTML has loaded, set listeners to all interactive elements
document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // On Submit New Email button click
  document.querySelector("#compose-form").onsubmit = send_email;

  // Reply and Archive buttons on an email
  document.querySelector("#email-reply").addEventListener("click", reply_email);
  document
    .querySelector("#email-archive")
    .addEventListener("click", archive_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

// Function takes id and GET that email or mailbox
async function fetch_emails(id) {
  const fetchThis = `/emails/${id}`;
  const response = await fetch(fetchThis);
  return await response.json();
}

// Function loads the mailbox that user requested
async function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#open-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  // GET the content of the mailbox
  const emails = await fetch_emails(mailbox);

  // Add each email to the email to the HTML
  emails.forEach((email) => {
    // Default colors for the email preview
    let bckgrColor = "bg-white";
    let textColor = "text-black";
    // Change the colors if the email has been read
    if (email.read && mailbox !== "sent") {
      // Don't allow the sender to see if the recipient has read the email
      bckgrColor = "bg-secondary";
      textColor = "text-white";
    }
    // Construct the HTML for email preview
    let content = `<div class = "d-flex flex-row border justify-content-between py-1 px-3 m-2 ${bckgrColor} ${textColor}">
                    
                    <div> ${email.sender} </div>
                    <div> ${email.subject} </div>
                    <div> ${email.timestamp} </div>
        </div>`;

    const element = document.createElement("div");
    element.innerHTML = content; // Put the email preview in another div
    element.addEventListener("click", () => load_email(`${email.id}`)); // Add onclick listener to the email preview
    document.querySelector("#emails-view").append(element); // Add the email preview HTML to the page
  });
}

// Function display the form to compose and send an email
function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#open-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

// Function submits the email to the DB
async function send_email(event) {
  // POST the message to API
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      // get the values out of the HTML field values
      recipients: document.querySelector("#compose-recipients").value,
      subject: document.querySelector("#compose-subject").value,
      body: document.querySelector("#compose-body").value,
    }),
  })
    // When the response comes back
    .then((response) => response.json())
    .then((result) => {
      localStorage.clear(); // Clear cache so that Sent mailbox loads anew
      load_mailbox("sent"); // Load the Sent mailbox
    });
  event.preventDefault(); // Prevent the default behavior from loading Inbox
  return false; // Prevent the HTML POST
}

// Function sets the email flags and optionally redirects afterwards
// Pass in boolean to set the flags to or null for no change
// Pass in name of the mailbox to redirect to or null for no redirect
async function mark_email(id, archived, read, redirect) {
  // Construct the PUT request
  const fetchThis = `/emails/${id}`; //putting integer into a template will turn it to a string
  const json = {};
  if (archived !== null) {
    json.archived = archived;
  }
  if (read !== null) {
    json.read = read;
  }

  // Send the PUT request
  fetch(fetchThis, {
    method: "PUT",
    body: JSON.stringify(json),
  }).then((response) => {
    // Once returned, if redirect was requested, redirect user to that mailbox
    if (redirect) {
      localStorage.clear(); // Clear cache so that mailbox loads anew
      load_mailbox(redirect); // Execute redirect
    }
  });
}

// Function displays the entire contents of a single email
async function load_email(id) {
  // Hide the mailbox and display the email
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#open-view").style.display = "block";

  // Take id and GET that email
  const email = await fetch_emails(id);
  // Add email data to the HTML
  document.querySelector("#email-id").innerHTML = email.id;
  document.querySelector("#email-time").innerHTML = email.timestamp;
  document.querySelector("#email-sender").innerHTML = email.sender;
  document.querySelector("#email-recipient").innerHTML = email.recipients;
  document.querySelector("#email-subject").innerHTML = email.subject;
  document.querySelector("#email-body").innerHTML = email.body;
  // Hide the email ID
  document.querySelector("#email-id").style.display = "none";

  // Hide Archive button for the sender
  const myName = document.querySelector("#mailbox-owner").innerHTML;
  if (email.sender === myName) {
    document.querySelector("#email-archive").style.display = "none";
  } else {
    // Set the button to visible otherwise, or it  will remain invisible forever
    document.querySelector("#email-archive").style.display = "inline";
  }

  // Set the appropriate text for Archive button
  if (email.archived) {
    document.querySelector("#email-archive").innerHTML = "Unarchive";
  } else {
    document.querySelector("#email-archive").innerHTML = "Archive";
  }

  // Mark the email as read
  mark_email(id, null, true, null);
}

// Function archives/unarchives an email
function archive_email() {
  // Get the email id from the hidden field
  const emailID = parseInt(document.querySelector("#email-id").innerHTML);
  // Get the text of the archive button
  const buttonText = document.querySelector("#email-archive").innerHTML;

  // Depending on the current text of the archive button - set to the opposite
  if (buttonText === "Unarchive") {
    mark_email(emailID, false, null, "inbox"); // redirect to inbox afterwards
  } else {
    mark_email(emailID, true, null, "inbox");
  }
}

// Function sends the email to Compose form and formats it for a response
async function reply_email() {
  // Get the email ID from the hidden field
  const emailID = document.querySelector("#email-id").innerHTML; // This is a string

  // Take id and GET that email
  const email = await fetch_emails(emailID); // This function expects a string

  // Display response form, hide other elements on the page
  compose_email();

  // Fill Compose email form with data from the email object
  document.querySelector("#compose-recipients").value = email.sender;
  // Add "Re: " in front of the subject if not already there
  let responseSubject = "";
  if (email.subject.slice(0, 4) === "Re: ") {
    responseSubject = email.subject;
  } else {
    responseSubject = "Re: " + email.subject;
  }
  document.querySelector("#compose-subject").value = responseSubject;

  // Set the response body with the timestamp and text of the previous email
  const responseBody = `On ${email.timestamp}  ${email.sender} wrote:\n${email.body}`;
  document.querySelector("#compose-body").value = responseBody;
}
