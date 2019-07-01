"use strict";

var cards = [document.getElementById('card1'), document.getElementById('card2'),
              document.getElementById('card3'), document.getElementById('card4'),
              document.getElementById('card5'), document.getElementById('card6'),
              document.getElementById('card7'), document.getElementById('card8'),
              document.getElementById('card9'), document.getElementById('card10'),
              document.getElementById('card11'), document.getElementById('card12')];
var hasFlippedCard = false;
var lockBoard = false;
var firstCard, secondCard;
var timerStart = Date.now();
var timerPassed;
var counter = 0;
var connectIndicator = document.getElementById("connection");

// if user is running mozilla then use it's built-in WebSocket
window.WebSocket = window.WebSocket || window.MozWebSocket;
// open connection
var connection = new WebSocket('ws://' + window.location.hostname + ':9581');

connection.onopen = function () {
  connectIndicator.innerHTML = "OK";
  console.log("Socket connected");
  var name = window.navigator.userAgent;
  try {
    name = name.split('(')[1].split(')')[0]
  } catch (e) {

  }

  connection.send("Hello! Connection from " + name)
};
connection.onerror = function (error) {
  connectIndicator.innerHTML = "NO";
};

connection.onmessage = function (message) {

};

function comfort() {
  console.log('comfort...');
}

function congratulate1() {
  console.log('congratulate...');
}

function congratulate2() {
  console.log('congratulate...');
} // game scripts


function flipCard() {
  if (lockBoard) return;
  if (this === firstCard) return;
  this.classList.add('flip');

  if (!hasFlippedCard) {
    // first click
    hasFlippedCard = true;
    firstCard = this;
    return;
  } 
  
  // second click
  secondCard = this;
  checkForMatch();
}

function checkForMatch() {
  var isMatch = firstCard.dataset.framework === secondCard.dataset.framework;
  isMatch ? disableCards() : unflipCards();
}

function disableCards() {
  congratulate1();
  console.log("Well done.");
  firstCard.removeEventListener('click', flipCard);
  secondCard.removeEventListener('click', flipCard);
  counter += 1;
  console.log(counter);

  if (counter === 6) {
    congratulate2();

    if (confirm("Would you like to restart the game?")) {
      setTimeout(function () {
        cards.forEach(function (card) {
          return card.classList.remove('flip');
        });
        cards.forEach(function (card) {
          return card.addEventListener('click', flipCard);
        });
      }, 500);
    }
  }

  resetBoard();
  timerStart = Date.now();
}

function unflipCards() {
  lockBoard = true;
  setTimeout(function () {
    firstCard.classList.remove('flip');
    secondCard.classList.remove('flip');
    resetBoard();
  }, 1500);
  timerPassed = Date.now() - timerStart; //console.log(timerPassed); 

  if (timerPassed >= 10000) {
    timerStart = Date.now(); // comfort

    console.log("Take your time. Don't worry.");
    comfort();
  }
}

function resetBoard() {
  hasFlippedCard = false;
  lockBoard = false;
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