document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 3000);
    });

    // Dynamic tournament filtering
    const tournamentFilter = document.getElementById('tournament-filter');
    if (tournamentFilter) {
        tournamentFilter.addEventListener('change', function() {
            const selectedTournamentId = this.value;
            const teamRows = document.querySelectorAll('.team-row');

            teamRows.forEach(row => {
                if (selectedTournamentId === 'all' || row.dataset.tournamentId === selectedTournamentId) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Team selection for matches
    const tournamentSelect = document.getElementById('tournament_id');
    const team1Select = document.getElementById('team1_id');
    const team2Select = document.getElementById('team2_id');
    
    if (tournamentSelect && team1Select && team2Select) {
        tournamentSelect.addEventListener('change', function() {
            const tournamentId = this.value;
            
            // Clear existing options
            team1Select.innerHTML = '<option value="">Select Team 1</option>';
            team2Select.innerHTML = '<option value="">Select Team 2</option>';
            
            if (tournamentId) {
                // Fetch teams for the selected tournament
                fetch(`/api/tournaments/${tournamentId}/teams`)
                    .then(response => response.json())
                    .then(teams => {
                        teams.forEach(team => {
                            const option = document.createElement('option');
                            option.value = team.id;
                            option.textContent = team.name;
                            
                            team1Select.appendChild(option.cloneNode(true));
                            team2Select.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching teams:', error));
            }
        });
        
        // Prevent selecting same team for both sides
        team1Select.addEventListener('change', function() {
            const selectedTeam = this.value;
            
            Array.from(team2Select.options).forEach(option => {
                if (option.value === selectedTeam) {
                    option.disabled = true;
                } else {
                    option.disabled = false;
                }
            });
        });
        
        team2Select.addEventListener('change', function() {
            const selectedTeam = this.value;
            
            Array.from(team1Select.options).forEach(option => {
                if (option.value === selectedTeam) {
                    option.disabled = true;
                } else {
                    option.disabled = false;
                }
            });
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('invalid');
                    
                    // Create or update error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
                } else {
                    field.classList.remove('invalid');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });

    // Live scoreboard updates for in-progress matches
    const scoreboardElements = document.querySelectorAll('.live-scoreboard');
    if (scoreboardElements.length > 0) {
        // Poll for updates every 30 seconds
        setInterval(() => {
            scoreboardElements.forEach(scoreboard => {
                const matchId = scoreboard.dataset.matchId;
                fetch(`/api/matches/${matchId}/score`)
                    .then(response => response.json())
                    .then(data => {
                        const team1Score = scoreboard.querySelector('.team1-score');
                        const team2Score = scoreboard.querySelector('.team2-score');
                        
                        if (team1Score && team2Score) {
                            team1Score.textContent = data.team1_score;
                            team2Score.textContent = data.team2_score;
                        }
                    })
                    .catch(error => console.error('Error updating scoreboard:', error));
            });
        }, 30000);
    }
});
