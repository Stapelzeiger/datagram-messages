# Datagram Messages

## Format

The messages are encoded using MessagePack and follow the following structure:

```
[ MESSAGE_NAME, ARG ]
```

where ```MESSAGE_NAME``` is the name (type) of the message and ```ARG``` is the
argument (payload) of the message.

## Reserved Message Names

The following message names are reserved for protocol use:

- req (used for service call reqests)
- res (used for service call responses)

## Service Call Message Format

Service call messages look like the following:

```
[ 'req', [ SERVICE_NAME, UUID, ARG] ]
```

where ```SERVICE_NAME``` is the name of the service that is requested,
```UUID``` is a unique identifyer for this request-response exchange and
```ARG``` is the request argument/payload.

The corresponding the reply looks like:

```
[ 'res', [ SERVICE_NAME, UUID, ARG] ]
```

where ```SERVICE_NAME``` and ```UUID``` are the same as in the request and
```ARG``` is the response payload. The UUID is used to attribute
the response message to the corresponding request call on the caller side.
