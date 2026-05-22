from scanbackup.domain import BBIPRepository, BBIPEntity


class MongoBBIPRepository(BBIPRepository):
    def update_info(self, table: str, data: list[BBIPEntity]) -> None:
        return super().update_info(table, data)

    def get_all(self, table: str) -> BBIPEntity:
        return super().get_all(table)

    def get_by_range_date(
        self,
        table: str,
        initial_date: str,
        final_date: str,
        initial_time: str | None = None,
        final_time: str | None = None,
    ) -> BBIPEntity:
        return super().get_by_range_date(
            table, initial_date, final_date, initial_time, final_time
        )
