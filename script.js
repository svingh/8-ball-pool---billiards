$(document).ready(function() {
    var isDragging = false;
    var cueBall = $('#cue-ball'); 
    var directionLine = $('#direction-line');
    var tableSvg = $('#table-svg');
    var namesUpdated = false;

    function updateTurnInfo() {
        if (isPlayer1Turn) {
            $('#player1').addClass('active-turn');
            $('#player2').removeClass('active-turn');
        } else {
            $('#player2').addClass('active-turn');
            $('#player1').removeClass('active-turn');
        }
    }

    function toggleTurn() {
        isPlayer1Turn = !isPlayer1Turn;
        updateTurnInfo();
    }

    updateTurnInfo();

    function updateBallAssignments(player1Balls, player2Balls) {
        if (player1Balls || player2Balls) {
            const ballGroupText = (balls) => balls === 'high' ? 'High Balls' : 'Low Balls';
            
            $('#player1').append(`<div class="ball-assignment">${ballGroupText(player1Balls)}</div>`);
            $('#player2').append(`<div class="ball-assignment">${ballGroupText(player2Balls)}</div>`);
        }
    }


    function updateDirectionLinePosition() {
        cueBall = $('#cue-ball');
        directionLine = $('#direction-line');
        directionLine.attr({
            x1: cueBall.attr('cx'),
            y1: cueBall.attr('cy')
        });
    }

    function simulateShot(velX, velY) {
        var cueX = cueBall.attr('cx');
        var cueY = cueBall.attr('cy');
        $.post('/shot', { velX: velX, velY: velY, cueX: cueX, cueY: cueY }, function(data) {
            if (data.status === 'Success') {
                animateFrames(data.svgFiles, data.gameOver ? () => displayWinner(data.winner) : null);
                if (!namesUpdated) {
                    $('#player1').text(data.player1Name);
                    $('#player2').text(data.player2Name);
                    namesUpdated = true; // Set the flag to true after updating names
                }
                if (!data.extraTurn) {
                    toggleTurn();
                }
                updateBallAssignments(data.player1Balls, data.player2Balls);
            } else {
                alert('There was an error simulating the shot.');
            }
        });
    }

    function displayWinner(winner) {
        var modal = document.getElementById('winnerModal');
        var winnerAnnouncement = document.getElementById('winnerAnnouncement');
        var restartGameButton = document.getElementById('restartGame');
      
        winnerAnnouncement.innerText = winner + " wins!";
        modal.style.display = "block";
      
        restartGameButton.onclick = function() {
          modal.style.display = "none";
          window.location.href = '/game-setup'; 
        }
      }
    

    tableSvg.on('mousedown', function(e) {
        if ($(e.target).is(cueBall)) {
            isDragging = true;
            updateDirectionLinePosition();
        }
    });

    $(window).on('mousemove', function(e) {
        if (isDragging) {
            directionLine.attr('visibility', 'visible');
            var offset = tableSvg.offset();
            var scale = tableSvg.width() / 1350;
            var mouseX = (e.pageX - offset.left) / scale;
            var mouseY = (e.pageY - offset.top) / scale;

            directionLine.attr({
                x2: mouseX,
                y2: mouseY
            });
        }
    });

    $(window).on('mouseup', function(e) {
        directionLine.attr('visibility', 'hidden');
        if (isDragging) {
            isDragging = false;

            var endX = parseFloat(directionLine.attr('x2'));
            var endY = parseFloat(directionLine.attr('y2'));

            var velX = (parseFloat(cueBall.attr('cx')) - endX) * 10;
            var velY = (parseFloat(cueBall.attr('cy')) - endY) * 10;

            velX = Math.max(Math.min(velX, 8000), -8000);
            velY = Math.max(Math.min(velY, 8000), -8000);

            simulateShot(velX, velY);
            directionLine.attr('visibility', 'hidden');
        }
    });

    $('#quit-game').on('click', function() {
        window.location.href = '/game-setup'; // Redirect to the game setup page
    });
    

    function animateFrames(svgContentsArray, callback) {
        let frameIndex = 0;
        const animationInterval = setInterval(() => {
            if (frameIndex < svgContentsArray.length) {
                tableSvg.html(svgContentsArray[frameIndex]);
                updateDirectionLinePosition();
                frameIndex++;
            } else {
                clearInterval(animationInterval);
                directionLine.attr('visibility', 'hidden');
                if (callback) {
                    callback();
                }
            }
        }, 15); // Animation speed in milliseconds
    }

    updateDirectionLinePosition();
});
