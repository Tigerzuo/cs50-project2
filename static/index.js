var socket = io.connect("https://cs50-flask-messenger.herokuapp.com",{secure: true},{transports: ['websocket']});

socket.on('connect', function () {
    var form = $('form.new_message').on('submit', function (e) {
        e.preventDefault()
        let user_input = $('input.message').val()
        socket.emit('new message', {
            message: user_input
        })
        $('input.message').val('').focus()
    })
})
socket.on('my response', function (msg) {
    console.log(msg)
    $('h3').remove()
    $('div.message_holder').append('<div><b style="color: #000">' + msg.username + ':' + '</b> ' + msg.message + '</div>')
})
