from datetime import UTC, datetime

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import DatabaseError
from interface_sync.models import LayerResult, PageResult
from interface_sync.persistence import InterfaceRepository
from interface_sync.synchronization.change_reporter import ChangeReporter
from interface_sync.synchronization.interface_change_planner import InterfaceChangePlanner
from interface_sync.utils.logger import ServiceLogger


class LayerDecommissioner:
    """Decommissions, once all pages are processed, the interfaces that disappeared [RF-009].

    A layer is evaluated only when every one of its pages succeeded; otherwise a failed page
    could be hiding interfaces and nothing of that layer is touched [RF-010]. An interface
    is present when its `scan_url` appears in any page of its layer.
    """

    def __init__(
        self,
        repository: InterfaceRepository,
        planner: InterfaceChangePlanner,
        change_reporter: ChangeReporter,
        logger: ServiceLogger,
    ) -> None:
        """Receive the collaborators of the layer decommission."""
        self._repository = repository
        self._planner = planner
        self._change_reporter = change_reporter
        self._logger = logger

    def decommission(self, page_results: list[PageResult]) -> list[LayerResult]:
        """Return one result per layer, in the order the layers first appear in the pages."""
        results_by_layer: dict[str, list[PageResult]] = {}
        for page_result in page_results:
            results_by_layer.setdefault(page_result.layer, []).append(page_result)
        return [
            self._decommission_layer(layer, layer_results)
            for layer, layer_results in results_by_layer.items()
        ]

    def _decommission_layer(self, layer: str, page_results: list[PageResult]) -> LayerResult:
        """Decommission one layer, or skip it when any of its pages failed."""
        failed_labels = [result.page_label for result in page_results if not result.succeeded]
        if failed_labels:
            reason = f"páginas fallidas: {', '.join(failed_labels)}"
            self._logger.warning(LogEvent.LAYER_SKIPPED, f"{layer} | {reason}")
            return LayerResult(layer=layer, skipped_reason=reason)

        present_scan_urls = frozenset().union(
            *(result.present_scan_urls for result in page_results)
        )
        try:
            active_interfaces = self._repository.find_active_by_layer(layer)
            changes = self._planner.plan_decommission(
                active_interfaces, present_scan_urls, datetime.now(UTC)
            )
            self._repository.apply(changes)
        except DatabaseError as error:
            self._logger.error(
                LogEvent.DATABASE_FAILED, f"{layer} | desincorporación | {error.cause}"
            )
            return LayerResult(layer=layer, database_cause=error.cause)

        self._change_reporter.report(changes)
        self._logger.info(
            LogEvent.LAYER_SUMMARY,
            f"{layer} | desincorporadas: {changes.decommissioned_count} | "
            f"sin cambios: {changes.unchanged_count}",
        )
        return LayerResult(layer=layer, decommissioned_count=changes.decommissioned_count)
