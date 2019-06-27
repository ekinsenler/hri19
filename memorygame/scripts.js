var ip=window.location.hostname;

const cards = document.querySelectorAll('.memory-card');

let hasFlippedCard = false;
let lockBoard = false;
let firstCard, secondCard;
let timerStart = Date.now();
let timerPassed;
let counter = 0;

//websocketserver connection
if (ip=='')
    ip='127.0.0.1';
port = 9100;

console.log("Trying connection...")
wsrobot_init(ip,port);

var codeport = 9010;
var codeurl = "ws://"+ip+":"+codeport+"/websocketserver";
console.log(codeurl);
codews = new WebSocket(codeurl);

var ctrlport = 9110;
var ctrlurl = "ws://"+ip+":"+ctrlport+"/ctrlwebsocketserver";
console.log(ctrlurl);
ctrlws = new WebSocket(ctrlurl);

function comfort() {
  console.log('comfort...');
  code = "\n" +
    //"begin()\n" +
    //"robot.say('Take your time. I am sure you can do it if you try harder.')" +
    "im.executeModality('TEXT_default','Take your time.')\n";
    //"end()\n";
  codews.send(code);
}

function congratulate1() {
  console.log('congratulate...');
  code = "\n" +
    //"begin()\n" +
    //"robot.say('Well done.')" +
    "im.executeModality('TEXT_default','Well done.')\n";
    //"end()\n";
  codews.send(code);
}

function congratulate2() {
  console.log('congratulate...');
  code = "\n" +
    //"begin()\n" +
    //"robot.say('Your worked hard and succeeded.')" +
    "im.executeModality('TEXT_default','You win!')\n";
    //"end()\n";
  codews.send(code);
}

// game scripts
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
  let isMatch = firstCard.dataset.framework === secondCard.dataset.framework;

  isMatch ? disableCards() : unflipCards();
}

function disableCards() {
  congratulate1();
  console.log("Well done.");
  
  firstCard.removeEventListener('click', flipCard);
  secondCard.removeEventListener('click', flipCard);

  counter+=1
  console.log(counter);
  if (counter === 6) {
    congratulate2();
    if (confirm("Would you like to restart the game?")) {
      setTimeout(() => {
        cards.forEach(card => card.classList.remove('flip'));
        cards.forEach(card => card.addEventListener('click', flipCard));
      }, 500);
    }    
  }

  resetBoard();

  timerStart = Date.now();
}

function unflipCards() {
  lockBoard = true;

  setTimeout(() => {
    firstCard.classList.remove('flip');
    secondCard.classList.remove('flip');

    resetBoard();
  }, 1500);

  timerPassed =  Date.now() - timerStart;
  //console.log(timerPassed); 
  if (timerPassed >= 10000) {
    timerStart = Date.now();
    // comfort
    console.log("Take your time. Don't worry.");
    comfort();
  }
}

function resetBoard() {
  [hasFlippedCard, lockBoard] = [false, false];
  [firstCard, secondCard] = [null, null];
}

(function shuffle() {
  cards.forEach(card => {
    let randomPos = Math.floor(Math.random() * 12);
    card.style.order = randomPos;
  });
})();

cards.forEach(card => card.addEventListener('click', flipCard));
