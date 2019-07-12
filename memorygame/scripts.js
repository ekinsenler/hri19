"use strict";

var cards = [document.getElementById('card1'), document.getElementById('card2'),
              document.getElementById('card3'), document.getElementById('card4'),
              document.getElementById('card5'), document.getElementById('card6'),
              document.getElementById('card7'), document.getElementById('card8'),
              document.getElementById('card9'), document.getElementById('card10'),
              document.getElementById('card11'), document.getElementById('card12')];
var firstCard, secondCard;
var counter = 0;
var connectIndicator = document.getElementById("connection");
var sentWelcome = false;

// if user is running mozilla then use it's built-in WebSocket
window.WebSocket = window.WebSocket || window.MozWebSocket;

var connection = null;
var unflipTimeoutBinding = null;

function connect() {
  // open connection
  connection = new WebSocket('ws://' + window.location.hostname + ':9581');

  connection.onopen = function () {
    connectIndicator.innerHTML = "OK";
    console.log("Socket connected");
    var name = window.navigator.userAgent;
    try {
      name = name.split('(')[1].split(')')[0]
    } catch (e) {

    }

    connection.send("I'M " + name);
    if (!sentWelcome) {
      connection.send("GAME_INIT");
      sentWelcome = true;
    }
  };
  connection.onerror = function (error) {
    connectIndicator.innerHTML = "NO";
  };

  connection.onclose = function () {
    setTimeout(connect, 500)
  };

  connection.onmessage = function (message) {

  };
}

connect();

function congratulate1() {
  connection.send("GAME_GOOD_1")
}

function congratulate2() {
  connection.send("GAME_GOOD_2")
}

function onGameWin() {
  connection.send("GAME_WINNER")
}

function flipCard() {
  if (this.classList.contains('flip'))
      return;

  if (firstCard != null && secondCard != null) {
    // Clicked third card while 2 is flipped
    unflipCardsNow();
    this.classList.add('flip');
    firstCard = this;
  } else if (firstCard != null && secondCard == null) {
    this.classList.add('flip');
    secondCard = this;
    checkForMatch();
  } else {
    // No card flipped
    this.classList.add('flip');
    firstCard = this;
  }
}

function checkForMatch() {
  var isMatch = firstCard.dataset.framework === secondCard.dataset.framework;
  isMatch ? disableCards() : unflipCards();
}

function disableCards() {

  firstCard.removeEventListener('click', flipCard);
  secondCard.removeEventListener('click', flipCard);
  counter += 1;
  firstCard = null;
  secondCard = null;
  console.log("Disable");

  if (counter === 6) {

    cards.forEach(function (card) {
      return card.classList.remove('flip');
    });
    cards.forEach(function (card) {
      return card.addEventListener('click', flipCard);
    });

    onGameWin();
  } else {
    congratulate1();
  }
}

function unflipCards() {
  unflipTimeoutBinding = setTimeout(unflipCardsNow, 1500);
}

function unflipCardsNow() {
  if (unflipTimeoutBinding != null) {
    clearTimeout(unflipTimeoutBinding);
    unflipTimeoutBinding = null;
  }
  firstCard.classList.remove('flip');
  secondCard.classList.remove('flip');
  firstCard = null;
  secondCard = null;
}

(function shuffle() {
  cards.forEach(function (card) {
    var randomPos = Math.floor(Math.random() * 12);
    card.style.order = randomPos;
  });
})();

cards.forEach(function (card) {
  return card.addEventListener('click', flipCard);
});