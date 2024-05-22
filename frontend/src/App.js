import React, {useState, useEffect, useRef} from 'react';
import './App.css';

function App() {
    const [messages, setMessages] = useState('');
    const [urls, setUrls] = useState([]); /// Use a single string for messages
    const [input, setInput] = useState('');
    const ws = useRef(null);
    const chatWindowRef = useRef(null);
    const chatTopicRef = useRef(null);

    useEffect(() => {
        ws.current = new WebSocket('ws://localhost:8765');

        ws.current.onopen = () => console.log('WebSocket connection established');

        ws.current.onclose = () => console.log('WebSocket connection closed');

        ws.current.onmessage = (message) => {
            if (message.data === '~END~') {
                setMessages((prevMessages) => prevMessages + '\n\n');
                setTimeout(scrollToBottom, 100);
            } else if (message.data.startsWith('~URLS~')) {
                let urls = message.data.replace('~URLS~', '');
                let urlList = JSON.parse(urls);
                setUrls(urlList);
                setTimeout(scrollToBottom, 100);
            } else {
                setMessages((prevMessages) => prevMessages + message.data);
                setTimeout(scrollToBottom, 100);
            }
        };
        setTimeout(scrollToBottom, 100);
        return () => {
            ws.current.close();
        };

    }, []);

    const sendMessage = () => {
        if (input && ws.current) {
            ws.current.send(chatTopicRef.current.valueOf().value + "|" + input);
            setUrls([])
            setMessages((prevMessages) => prevMessages.replace('Here are some helpful links:', '').trim());
            if(messages !== ''){
                setMessages((prevMessages) => prevMessages + '\n\nMe: ' + input + '\n\n');
            } else {
                setMessages((prevMessages) => prevMessages + 'Me: ' + input + '\n\n');
            }

            setInput('');
            setTimeout(scrollToBottom, 100);
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
            <input className={'topicInput'} ref={chatTopicRef} defaultValue={'Dementia'}/>
            <div className="chat-window" ref={chatWindowRef}>
                <div className="chat-message">
                    {messages}
                    {urls.map(url => (
                        <React.Fragment key={url}><a rel={"noreferrer"} target={"_blank"}
                                                     href={url}>{url}</a><br/></React.Fragment>
                    ))}
                </div>
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
