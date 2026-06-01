def calculate_position_size(
    balance,
    risk_percent,
    entry,
    stop_loss
):

    risk_amount = balance * risk_percent

    position_size = (
        risk_amount /
        abs(entry - stop_loss)
    )

    return round(position_size, 4)
