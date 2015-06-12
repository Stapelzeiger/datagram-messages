This document describes a message and service call format for MessagePack encoded
datagrams.

# Messages

Messages are named packets sent without any guarantees about their delivery.

## Message Format

The messages are encoded using MessagePack and follow the following structure:
(Note: square brackets designate MessagePack arrays)

```
[ MESSAGE_NAME, ARG ]
```

where ```MESSAGE_NAME``` is an ASCII encoded string which represents the name (type) of the message and ```ARG``` is the MessagePack formatted argument (payload) of the message.

## Reserved Message Names

The following message names are reserved for protocol use:

- req (used for service call requests)
- res (used for service call responses)

# Service Calls

Service calls are named request-response connections.
When a service call is made it returns the response or a connection error.
This means that when no error is returned, the delivery is guaranteed.

## Service Call Format

Service call messages look like the following:

```
[ 'req', [ SERVICE_NAME, SEQ, ARG] ]
```

where ```SERVICE_NAME``` is the name (ASCII encoded) of the service that is requested, ```SEQ``` is a sequence number (32 bit unsigned integer) for this request-response exchange and ```ARG``` is the request argument/payload.

The corresponding the reply looks like:

```
[ 'res', [ SERVICE_NAME, SEQ, ARG] ]
```

where ```SERVICE_NAME``` and ```SEQ``` are the same as in the request and ```ARG``` is the response payload.
The SEQ is used to attribute the response message to the corresponding request call on the caller side.

## Sequence Numbers

The caller should use an incrementing sequence number for each call he makes to be able to associate the response messages to the requests.
The server shall make no assumptions on the contents of the sequence number.

## Retransmission Handling

There are two parameters for retransmission: the request _timeout_ and the _number of retries_.

When the client receives no response after _timeout_ has elapsed since the request has been sent, the request is re-sent.
This retransmission is repeated for a maximum number of times specified in _number of retries_.
When the _timeout_ is reached after re-sending for _number of retries_ times, the call shall return a connection error to the application.

When a client receives a response multiple times for the same sequence number (due to delay and retransmission) only the first response shall be returned to the application.

When a server receives a request with the same sequence number as an earlier request it handles the request normally.
This means that a service call can be executed multiple times for a single call.
For applications where this is problematic a service internal sequence number (passed as an argument) could be used.
