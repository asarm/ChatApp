document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        // Notify the server user has joined
        socket.emit('joined');
        document.querySelector('#message').addEventListener("keydown", event => {
            if (event.key === "Enter") {
                document.getElementById("send").click();
            }
        });

        // Send button emits a "message sent" event
        document.querySelector('#send').addEventListener("click", () => {
            // Save time in format HH:MM:SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Save user input
            let message = document.getElementById("message").value;

            socket.emit('send message', message, timestamp);

            // Clear input
            document.getElementById("message").value = '';
        });
    });

     socket.on('status', data => {
        // Broadcast message of joined user.
        let row = '<' + `${data.message}` + '>';
        document.querySelector('#chat').value += row + '\n';
        // Save user current channel on localStorage
        localStorage.setItem('last_channel', data.channel);
     });

    document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

    socket.on('announce message', data => {
        // Format message
        let row = '<' + `${data.timestamp}` + '> - ' + '[' + `${data.user}` + ']:  ' + `${data.message}`;
        document.querySelector('#chat').value += row + '\n';
});