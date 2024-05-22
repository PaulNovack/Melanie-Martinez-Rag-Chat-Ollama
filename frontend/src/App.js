import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
    const [messages, setMessages] = useState(''); // Use a single string for messages
    const [input, setInput] = useState('');
    const ws = useRef(null);
    const chatWindowRef = useRef(null);
    const chatTopicRef = useRef(null);

    useEffect(() => {
        // Replace with your WebSocket server URL
        ws.current = new WebSocket('ws://localhost:8765');

        ws.current.onopen = () => console.log('WebSocket connection established');
        ws.current.onclose = () => console.log('WebSocket connection closed');

        ws.current.onmessage = (message) => {
            if(message.data === '~END~'){
                setMessages((prevMessages) => prevMessages + '\n\n');
                scrollToBottom();
            } else {
                setMessages((prevMessages) => prevMessages + message.data);
                scrollToBottom();
            }
            console.log(message.data);
        };


        return () => {
            ws.current.close();
        };
    }, []);

    const sendMessage = () => {
        if (input && ws.current) {
            ws.current.send(chatTopicRef.current.valueOf().value + "|" + input);
            setMessages((prevMessages) => prevMessages + 'Me: ' + input + '\n\n');
                setInput('');
            scrollToBottom();
        }
    };

    const scrollToBottom = () => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    };

    return (
        <div className="App">
            <h1>Chat for Topic:</h1>
            <input className={'topicInput'} ref={chatTopicRef}  defaultValue={'Melanie_Martinez'}/>
            <div className="chat-window" ref={chatWindowRef}>
                <pre className="chat-message">{messages}</pre> {/* Display the entire message string */}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
}

export default App;
