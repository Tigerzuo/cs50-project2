var socket = io.connect('/',{secure: true});

socket.on('connect', function () {
    var form = $('form.new_message').on('submit', function (e) {
        e.preventDefault()
        let user_input = $('input.message').val()
        socket.emit('my event', {
            message: user_input
        })
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
