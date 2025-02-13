# vue-stub

## Why

I needed a quick and dirty FastAPI + Vue skeleton to illustrate a few techniques.

## What

This creates two server-side background tasks that mock monitoring a database table and calling an external API (it's actually calling itself for the sake of simplicity), and sends live events to a simple Vue front-end, demonstrating how to integrate back-end asynchronous "processing" with a Vue app.

For a quick encore, it also generates PDFs. It's all using mostly the same database query for simplicity, but it's the makings of a simple AI front-end.

## How

```bash
make deps
make init-db
make serve
```

## To Do

Things this _does not do_:

- [ ] Caching (sane people would add some immediately, even if only in-process)
- [ ] Authentication
- [ ] External database queries (I decided to do a quick conversion of the classic Northwind Traders database to `sqlite`, for fun)
- [ ] External API calls (it actually calls itself)
- [ ] External queues/event sources (like what you might get from an Azure Function/Redis/etc.)
- [x] Basic multi-client support
- [ ] Session management
- [ ] Proper dependency management (version pinning, `virtualenv`, etc.)
