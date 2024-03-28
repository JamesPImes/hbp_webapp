
# HBP Web App

A web application for checking for periods of time during which oil
wells or gas wells ceased producing, to help determine whether an oil
and gas lease remains "Held By Production" (or simply "HBP").


## Why?

Borrowing the following explanation from a write-up I did for a 
[related project](https://github.com/JamesPImes/og_production_analyzer)
(which is also used in this project):

> An "oil and gas lease" is a contract between a landowner and an oil company
that lays out the terms for the company to drill wells on the land, the
royalties they must pay to the landowner, etc.
> 
> A typical lease is negotiated to last a specific period of time (e.g., 1 year,
5 years, whatever gets negotiated) -- __and then to continue indefinitely,
for as long as oil and/or gas are produced from one or more wells on the
leased lands.__
Without consistent production, the lease will automatically terminate.
The lease will often specify just how consistent the production must be
-- commonly allowing up to 90 consecutive days before expiration.
It might also specify the *quantity* of oil or gas to be produced in order
to extend the lease indefinitely. If sufficient production resumes soon
enough, the termination timer is reset to 90 days (or whatever was
negotiated).
> 
> However, it is not always obvious to either party when production has
ceased and a lease has terminated -- especially when there are many wells
to check, multiple leases to keep track of, and decades have passed.
(When a lease termination isn't noticed, the company may need to negotiate
some sort of resolution or face litigation, if production is resumed late
or new wells are drilled without a valid lease in place -- and those risks
and penalties may compound as time goes on.)

In short, if all of the relevant wells cease producing oil or gas during
the same period of time, a lease might terminate if that cessation lasts
long enough. This web application analyzes the publicly available
production records for the requested wells and reports any such periods
of zero production and the duration of each.
